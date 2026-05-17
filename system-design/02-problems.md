# System Design Practice — Problems & Plan

> **Open this to pick what to practice today.** Star (★) marks problems most commonly asked at SDE 2.

---

## Problem Bank (Ordered by Difficulty)

Aim for ~20 problems over 4-6 weeks.

### Tier 1 — Foundational (do these first)

1. **★ URL shortener (bit.ly)** — encoding scheme, collision handling, redirect path, analytics
2. **★ Pastebin** — write-once-read-many, expiration, blob vs DB storage
3. **★ Rate limiter** — token bucket vs leaky bucket vs sliding window; distributed via Redis
4. **★ Key-value store** — consistent hashing, replication, quorum reads/writes
5. **Web crawler** — URL frontier, politeness, dedup, distributed coordination
6. **Unique ID generator** — Snowflake, UUID v7, range-based allocation tradeoffs

### Tier 2 — Core social/consumer (FAANG bread & butter)

7. **★ News feed (Twitter/Facebook)** — push (fan-out on write) vs pull (fan-out on read), celebrity problem
8. **★ Chat system (WhatsApp/Slack)** — long-poll vs WebSocket, message ordering, online presence
9. **★ Notification system** — multi-channel (push/email/SMS), retries, dedup, user preferences
10. **Instagram / photo sharing** — image upload pipeline, CDN, feed
11. **YouTube / video streaming** — chunked upload, transcoding pipeline, adaptive bitrate, CDN
12. **Search autocomplete** — trie, weighted suggestions, personalization, latency budget

### Tier 3 — Location, marketplace, real-time

13. **★ Uber / ride-sharing** — geo-indexing (quadtree, geohash, H3), driver-rider matching, surge
14. **Yelp / nearby places** — geo-search, ranking, caching
15. **Ticketmaster / seat booking** — inventory locks, fairness, fraud, sudden traffic spikes
16. **Stock exchange / order matching** — matching engine, latency, durability, sequencing

### Tier 4 — Infra & data-heavy

17. **Distributed cache** — eviction, replication, hot keys
18. **Distributed task scheduler (cron)** — leader election, at-least-once, exactly-once
19. **Metrics / monitoring system** — time-series ingest, aggregation, retention tiering
20. **Google Drive / Dropbox** — file sync, chunking, dedup, conflict resolution

### What to expect at SDE 2

Most interviews pull from Tier 1 and Tier 2. You should be able to do those in your sleep. Tier 3 differentiates strong candidates. Tier 4 is bonus — useful but not required to clear the bar.

---

## 6-Week Practice Plan

### Week 1 — Re-internalize the framework
- Re-read Xu Chapter 1-4 (back-of-envelope, framework, rate limiter, consistent hashing).
- Do problems 1, 3, 4. Use the template from the Process doc. No peeking.

### Week 2 — Foundational fluency
- Do problems 2, 5, 6.
- Re-do problem 1 from memory; compare to your Week 1 attempt.

### Week 3 — Core consumer
- Do problems 7, 8, 9. These are the most common SDE 2 questions.
- Start one mock interview (Pramp or a friend).

### Week 4 — Media and search
- Do problems 10, 11, 12.
- Re-do problem 7 from memory.
- One more mock.

### Week 5 — Real-time and geo
- Do problems 13, 14, 15.
- Two mocks this week.

### Week 6 — Infra + review
- Do 1-2 from Tier 4 if time.
- Re-do problems 8, 13 from memory.
- Two final mocks.
- Re-read your Practice Log; identify your weakest pattern and drill it.

---

## Practice Log

> Fill this in after every session. The **Re-do by** column is what makes problems stick — a problem re-done from memory 2 weeks later teaches more than a new one.

| Date | Problem | Time | What went well | What I missed | Re-do by |
|---|---|---|---|---|---|
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
|   |   |   |   |   |   |
