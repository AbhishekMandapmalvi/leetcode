# Chapter 11: Design A News Feed System

A news feed shows a continuously updating list of posts from people you follow, newest-first. The whole problem splits into two flows: **publishing** a post (fanout) and **building** a user's feed (retrieval).

```
   Alice posts ──► [Publish flow] ──► fanout to followers' feeds
   Bob opens app ──► [Build flow] ──► assemble + hydrate ──► render
```

---

## Two flows

### Feed publishing flow

```
   ┌────────┐  POST /feed   ┌──────────────┐      ┌─────────────┐
   │ Client │ ─────────────►│  Web servers │ ────►│ Post service│ ─► Post DB/cache
   └────────┘               │ (auth, rate) │      └─────┬───────┘
                            └──────────────┘            │
                                                        ▼
                                              ┌───────────────────┐
                                              │   Fanout service  │ ─► Fanout workers
                                              └───────────────────┘     via message queue
                                                        │
                                              writes post_id into each
                                              follower's news-feed cache
```

### Feed build (retrieval) flow

```
   ┌────────┐ GET /feed     ┌──────────────┐   ┌────────────────────┐
   │ Client │ ─────────────►│  Web servers │ ─►│  News feed service │
   └────────┘               └──────────────┘   └─────────┬──────────┘
                                                          ▼
                                       read post_id list from news-feed cache
                                                          ▼
                                       hydrate: content cache, social-graph
                                       cache, action cache, counter cache
                                                          ▼
                                       fully built feed ──► back to client
```

The split matters: heavy work (fanout) happens on **write** so reads are cheap; or vice-versa. That choice is the fanout model.

---

## Fanout service

Fanout = delivering a new post to all the people who should see it. Three strategies:

### Fanout on write (push model)

When a user posts, **immediately** push the `post_id` into every follower's news-feed cache. Reads are then a trivial cache lookup.

```
   Alice posts ──► fanout workers ──► for each follower f:
                                        newsfeed_cache[f].prepend(post_id)

   Follower reads feed = O(1) cache read   (pre-computed)
```

- **Pro:** feed read is real-time and very fast (already materialized).
- **Con:** **hot-key / fanout storm** — a celebrity with 100M followers triggers 100M writes per post. Wastes work on inactive users. Slow for users who follow many people who all post.

### Fanout on read (pull model)

Do nothing on write. When a user opens the app, **pull** recent posts from everyone they follow and merge on the fly.

```
   Bob opens app ──► get followees ──► for each: fetch recent posts
                  ──► merge + sort by time ──► feed
```

- **Pro:** no wasted work for inactive users; no celebrity write storm; storage-light.
- **Con:** read is **slow** (fan-in query + merge across many followees on every request).

### Hybrid (the answer)

```
   Regular user posts        → fanout-on-write (push to followers' caches)
   Celebrity posts           → do NOT fan out
   At read time:               base feed (pushed) + pull celebrity posts
                                ──► merge ──► final feed
```

Most users get pre-computed feeds (fast); celebrities skip the write storm; their followers pull celebrity posts at read time and merge. Best of both — this is the production answer.

| Model              | Write cost      | Read cost     | Best for                  | Problem                       |
| ------------------ | --------------- | ------------- | ------------------------- | ----------------------------- |
| Fanout on write    | High (×followers) | O(1)        | Most users, fast reads    | Celebrity fanout storm        |
| Fanout on read     | O(1)            | High (fan-in) | Celebrities, inactive users | Slow, expensive reads        |
| **Hybrid**         | Mixed           | Mixed         | Real systems              | Added merge complexity        |

---

## Cache architecture (five layers)

Aggressive caching is what makes this feasible. The book splits cache into five purpose-built tiers:

```
   ┌────────────────────────────────────────────────────┐
   │ 1. News feed cache  : user_id → [post_id, post_id…] │
   ├────────────────────────────────────────────────────┤
   │ 2. Content cache    : post_id → post object         │
   │      ├─ hot     : viral / very popular posts        │
   │      └─ normal   : the long tail                    │
   ├────────────────────────────────────────────────────┤
   │ 3. Social graph cache : user_id → followers/followees│
   ├────────────────────────────────────────────────────┤
   │ 4. Action cache     : has this user liked/commented?│
   ├────────────────────────────────────────────────────┤
   │ 5. Counter cache    : like / reply / follower counts│
   └────────────────────────────────────────────────────┘
```

| Cache         | Key → value                          | Why separate                                    |
| ------------- | ------------------------------------ | ----------------------------------------------- |
| News feed     | `user_id → list<post_id>`            | Materialized feed; only IDs (small, fast)        |
| Content hot   | `post_id → post` (viral)             | Hot posts read by millions → dedicated tier      |
| Content normal| `post_id → post` (long tail)         | Bulk of posts, lower QPS, can use cheaper tier   |
| Social graph  | `user_id → followers / followees`    | Fanout + pull both need the graph constantly     |
| Action        | `(user, post) → liked? replied?`     | Per-viewer state to render UI correctly          |
| Counter       | `post_id → {likes, replies, …}`      | Hot counters change fast; isolate write pressure |

The news-feed cache stores only `post_id`s, not full posts — keeps it tiny and lets many users share one cached post object (content cache). Splitting **hot vs normal** content lets viral posts get more replicas/memory without bloating the long tail.

---

## News feed retrieval API (cursor pagination)

Feeds are infinite scroll. **Do not use offset/limit** — offset pagination breaks when new posts arrive (items shift, duplicates/skips). Use **cursor pagination**: the cursor encodes the last-seen position (e.g. last post_id or timestamp).

```
   GET /v1/me/feed?limit=20
     → { items:[...20], next_cursor:"eyJ0cyI6MTY4..." }

   GET /v1/me/feed?limit=20&cursor=eyJ0cyI6MTY4...
     → next page, stable even if new posts were published meanwhile
```

- **Stable** under inserts (new posts go on top, don't shift the cursor's window).
- **Efficient** — `WHERE id < cursor ORDER BY id DESC LIMIT n` uses the index; no scanning skipped rows.
- Cursor is opaque/base64-encoded so clients don't depend on its internals.

---

## Full architecture

```
   ┌────────┐        ┌──────────────┐   ┌────────────────┐
   │ Client │ ─────► │ Web servers  │ ─►│ Post service   │ ─► Post DB + content cache
   └────────┘        │ auth · rate  │   └───────┬────────┘
        ▲            └──────────────┘           │ publish event
        │                                       ▼
        │                          ┌──────────────────────┐
        │                          │   Message queue       │
        │                          └──────────┬────────────┘
        │                                     ▼
        │                          ┌──────────────────────┐
        │                          │   Fanout workers     │ ─► news-feed cache
        │                          └──────────────────────┘     (per follower)
        │                                     │
        │                                     ▼
        │                          ┌──────────────────────┐
        │                          │ Notification service │ ─► push to followers
        │                          └──────────────────────┘
        │
        │  GET feed   ┌────────────────────┐
        └─────────────│ News feed service  │ ─► read 5 caches, hydrate, return
                      └────────────────────┘
```

- **Web servers** — auth, rate limiting, request routing; the public edge.
- **Post service** — persists the post (DB + content cache), emits a publish event.
- **Message queue** — decouples publish from fanout; absorbs spikes; lets fanout workers scale independently.
- **Fanout workers** — consume publish events, read the social graph, write `post_id` into each follower's news-feed cache (skip celebrities → hybrid).
- **Notification service** — pushes "new post" alerts (Ch10) to followers.
- **News feed service** — on read, fetches the feed cache, then hydrates content/graph/action/counter caches into a fully rendered feed.

---

## Hot-key & scaling trade-offs

- **Celebrity hot key** — handled by the hybrid model: skip fanout-on-write for high-follower accounts; pull their posts at read time.
- **News-feed cache size** — store only IDs; cap list length (e.g. last ~1000 post_ids) — nobody scrolls infinitely; older pages fall back to DB.
- **Sharding** — shard caches/DB by `user_id`; replicate read-heavy caches; keep counter cache on its own tier (write-hot).
- **Inactive users** — fanout-on-write wastes work on users who never log in; lazily skip or shorten retention for inactive accounts.
- **Consistency** — feeds are **eventually consistent**; a few seconds of fanout lag is acceptable for a social feed.
- **DB choice** — relational for users/posts is fine at first; scale via vertical/horizontal sharding and replication; caches absorb the bulk of read QPS.

---

## Real-world usage

- **Facebook / Instagram** — hybrid fanout; aggressive multi-tier caching (this chapter mirrors their design).
- **Twitter/X** — famous hybrid "fanout-on-write + pull for high-fanout accounts" timeline.
- **Redis** — typical store for news-feed cache (lists/sorted sets) and counters.
- **Kafka / RabbitMQ** — the publish→fanout message queue backbone.

---

## One-page summary

```
   GOAL: newest-first feed of followed users, fast reads at scale

   FLOWS:   publish (post → fanout) ;  build (read caches → hydrate → render)
   FANOUT:  push (write-heavy, fast read)  vs  pull (read-heavy)
            → HYBRID: push for normal users, pull for celebrities, merge on read
   CACHES:  feed · content(hot/normal) · social-graph · action · counter
   API:     cursor pagination (stable under inserts, index-friendly)
   INFRA:   web svrs · post svc · message queue · fanout workers · notif svc
   HOT KEY: celebrity storm → hybrid;  feed cache = post_ids only, capped
   CONSIST: eventually consistent feed is acceptable
```

## Notes
_Add your own notes here._
