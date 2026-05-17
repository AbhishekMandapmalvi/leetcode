# Chapter 9: Design A Web Crawler

A web crawler (spider/bot) starts from **seed URLs**, downloads pages, extracts links, and recursively visits them — feeding a search index, archive, or data pipeline. The interesting parts are scale, politeness, and not getting trapped.

```
   seed URLs ─► download page ─► parse ─► extract links ─► filter ─► enqueue
        ▲                                                              │
        └──────────────────────────────────────────────────────────────┘
                         (BFS over the web graph)
```

---

## Use cases

| Use case               | What the crawler feeds                              |
| ---------------------- | --------------------------------------------------- |
| **Search indexing**    | Googlebot/Bingbot → inverted index                  |
| **Web archiving**      | Wayback Machine — snapshot the web over time        |
| **Web mining**         | data for ML, price/news aggregation, research       |
| **Web monitoring**     | watch for copyright/piracy, defacement, changes     |

Clarify in interview: how many pages, how often (freshness), what content types (HTML only? PDFs/images?), how long stored, dedupe robustness.

---

## Characteristics (the four pillars)

| Property        | What it means                                                          |
| --------------- | ---------------------------------------------------------------------- |
| **Scalability** | billions of pages — must parallelize/distribute                        |
| **Robustness**  | survive bad HTML, traps, crashes, unresponsive servers                 |
| **Politeness**  | don't hammer one site; respect `robots.txt` and crawl delay            |
| **Extensibility** | plug in new content types/modules without a rewrite                  |

### Back-of-the-envelope estimation

Assume **1 billion** pages crawled per month, average page **~500 KB**.

```
   QPS (avg)  = 1,000,000,000 / (30 × 86,400) ≈ 400 pages/sec
   QPS (peak) ≈ 2 × avg ≈ 800 pages/sec
   Storage/mo = 1e9 × 500 KB ≈ 500 TB/month
   Storage/5yr ≈ 500 TB × 12 × 5 ≈ 30 PB
```

| Metric           | Value (approx)     |
| ---------------- | ------------------ |
| Pages / month    | 1 billion          |
| Avg page size    | ~500 KB            |
| Crawl rate (avg) | ~400 pages/sec     |
| Storage / month  | ~500 TB            |
| Storage / 5 yr   | ~30 PB             |

Takeaway: PB-scale storage (blob store) + a massively parallel, host-sharded crawl fleet are non-negotiable.

---

## High-level design

```
                     ┌──────────────┐
   Seed URLs ───────►│ URL Frontier │◄──────────────────────────┐
                     └──────┬───────┘                            │
                            ▼                                    │
                   ┌──────────────────┐     ┌────────────────┐   │
                   │  HTML Downloader  │◄───►│  DNS Resolver  │   │
                   └────────┬─────────┘      └────────────────┘   │
                            ▼                                     │
                   ┌──────────────────┐                           │
                   │  Content Parser  │                           │
                   └────────┬─────────┘                           │
                            ▼                                      │
                   ┌──────────────────┐  seen   (drop duplicate)  │
                   │  Content Seen?   │────────────────────────►  │
                   └────────┬─────────┘                           │
                       new  ▼                                      │
                   ┌──────────────────┐    ┌──────────────────┐    │
                   │ Content Storage  │    │  URL Extractor   │    │
                   └──────────────────┘    └────────┬─────────┘    │
                                                    ▼              │
                                           ┌──────────────────┐    │
                                           │   URL Filter     │    │
                                           └────────┬─────────┘    │
                                                    ▼              │
                                           ┌──────────────────┐    │
                                           │   URL Seen?      │    │
                                           └────────┬─────────┘    │
                                              not   ▼  seen → drop │
                                           ┌──────────────────┐    │
                                           │   URL Storage    │────┘
                                           └──────────────────┘
```

### Component responsibilities

| Component         | Responsibility                                                        |
| ----------------- | --------------------------------------------------------------------- |
| **Seed URLs**     | starting points; pick by popularity/topic/locale for good coverage    |
| **URL Frontier**  | the to-crawl queue; manages priority + politeness + freshness         |
| **HTML Downloader** | fetch the page over HTTP (respecting robots.txt)                    |
| **DNS Resolver**  | hostname → IP; cached because DNS is slow                             |
| **Content Parser**| parse + validate HTML (malformed pages waste resources)               |
| **Content Seen?** | dedupe page content (many URLs serve identical bytes)                 |
| **Content Storage** | persist pages; hot in memory, bulk on disk/blob                     |
| **URL Extractor** | pull out anchor links, resolve relative → absolute                   |
| **URL Filter**    | drop blocklisted/file-type/error URLs                                |
| **URL Seen?**     | have we already crawled/queued this URL? (Bloom filter / hash set)    |
| **URL Storage**   | persist discovered URLs                                               |

---

## Crawl algorithm: BFS

The web is a directed graph (pages = nodes, links = edges). Crawl = graph traversal. **BFS** (a FIFO queue = the URL frontier) is the standard choice over DFS — DFS can go arbitrarily deep down one site.

```
   queue: [seed]
   while queue not empty:
       url = queue.pop_front()
       html = download(url)
       store(html)
       for link in extract(html):
           if not seen(link): queue.push_back(link)
```

**Problems with naive BFS**
- **Impolite:** most links on a page point back to the *same host* → FIFO drains them back-to-back → you DoS that one server.
- **No priority:** a spam page and the homepage of a major site are treated equally.

→ Both fixed by a smarter frontier.

---

## URL Frontier (Mercator design)

The frontier enforces **politeness**, **priority**, and **freshness**. Mercator-style: two queue layers.

```
   ┌──────────────────── Front queues (PRIORITY) ─────────────────────┐
   │   prioritizer → f1 (high) f2 ... fn (low)                         │
   └───────────────┬──────────────────────────────────────────────────┘
                   │  (front queue selector: bias toward high priority)
                   ▼
   ┌──────────────────── Back queues (POLITENESS) ────────────────────┐
   │   b1   b2   b3 ...  bM     (exactly one host per back queue)      │
   │   ▲ mapping table: host → back queue id                          │
   └───────────────┬──────────────────────────────────────────────────┘
                   ▼
        min-heap of (next_fetch_time, queue_id)  ── worker pulls,
        sleeps until allowed, fetches, re-enqueues with a new delay
```

### Politeness
- One **back queue per host**; a worker thread is bound to a single back queue → only one connection to a host at a time.
- A delay between requests to the same host (e.g. honor `Crawl-delay` or add 1–N s).
- Min-heap tracks the earliest time each host may be hit again.

### Priority
- **Front queues** ranked by importance (PageRank, traffic, update frequency, domain authority).
- A *prioritizer* assigns each URL to a front queue; the selector dequeues more often from high-priority queues.

### Freshness
- Pages change → must **recrawl**. Recrawl frequency ∝ how often a page historically changes and how important it is (news site front page: minutes; a static doc: months).
- Use historical update stats; don't recrawl everything uniformly.

**Storage:** the frontier is huge (hundreds of millions of URLs). Keep the majority on disk; buffer enqueue/dequeue ends in memory.

---

## HTML Downloader

### robots.txt
Before fetching a host, download and cache its `/robots.txt` (Robots Exclusion Protocol). It declares which paths bots may not crawl. Respecting it is non-negotiable (legal + ethical + politeness). Cache it with a TTL to avoid re-fetching per URL.

```
   User-agent: *
   Disallow: /private/
   Crawl-delay: 2
```

### Performance optimization

| Technique              | Why                                                            |
| ---------------------- | -------------------------------------------------------------- |
| **Distributed crawl**  | shard URL space across many servers/threads (by host hash)     |
| **DNS cache**          | DNS lookups are slow (10s–100s ms, often synchronous) → cache  |
| **Locality**           | place crawl servers geographically near the sites they fetch   |
| **Short timeout**      | a slow host must not block a worker — cap wait, move on         |

```
   ┌──────┐  ┌──────┐  ┌──────┐   crawl workers
   │ W1   │  │ W2   │  │ W3   │   (host-sharded)
   └──┬───┘  └──┬───┘  └──┬───┘
      └─────────┼─────────┘
                ▼
        shared frontier + DNS cache + seen filters
```

---

## Content Seen? and URL Seen?

Two dedupe checks, both critical at scale.

- **Content Seen?** — ~30% of the web is duplicate content (mirrors, copies). Hash the page (e.g. checksum of the body) and look up in a set; skip storage/parse if already seen.
- **URL Seen?** — avoid re-crawling and infinite loops. A hash set of all URLs is enormous → use a **Bloom filter** (probabilistic, tiny memory, no false negatives, small false-positive rate is acceptable — worst case: skip a few legit URLs).

```
   page bytes ─► hash ─► in content-seen set? ─ yes ─► drop
   url       ─► Bloom filter ──────────────── present ─► drop (likely seen)
```

---

## Robustness

- **Consistent hashing** to distribute crawl load across downloaders and rebalance when a node dies (see Ch. 5).
- **Save crawl state** (frontier, seen filters) to durable storage → resume after a crash, no full restart.
- **Exception handling** — never let one bad page kill a worker; isolate and continue.
- **Data validation** — reject malformed/oversized responses early.

## Extensibility

Make the pipeline pluggable so new modules slot in without a rewrite (single-responsibility components connected by clear interfaces).

```
   download ─► [HTML parser] ─► ...
                  │
                  ├─► [PNG downloader module]   (add later)
                  ├─► [Web monitor module]      (add later)
                  └─► [PDF / RSS extractor]     (add later)
```

- Each box above is independently deployable and testable.
- Adding "crawl images too" = register a new content handler, no core change.

---

## Detect and avoid problematic content

| Problem            | Description                                       | Mitigation                                              |
| ------------------ | ------------------------------------------------- | ------------------------------------------------------- |
| **Redundancy**     | ~30% duplicate pages waste storage/compute        | content hashing / "Content Seen?"                       |
| **Spider traps**   | pages generating infinite URLs (e.g. deep calendar links, dynamic params) | max URL length, depth/host caps, manual blocklist, anomaly detection |
| **Spam / link farms** | pages built only to fool crawlers/PageRank      | URL filter, domain reputation, manual review            |
| **Data noise**     | ads, boilerplate, low-value content               | strip in content parser; don't index                    |

---

## Real-world usage

| Crawler             | Notes                                                       |
| ------------------- | ----------------------------------------------------------- |
| **Googlebot**       | massive distributed crawl, freshness-aware recrawl          |
| **Bingbot**         | Microsoft's search crawler                                  |
| **Internet Archive**| Heritrix crawler → Wayback Machine                          |
| **Common Crawl**    | open web-scale dataset (petabytes), widely used for ML      |
| **Apache Nutch**    | open-source crawler that influenced Hadoop                  |

---

## Trade-offs and gotchas

- **Politeness vs throughput** — per-host serialization limits speed; you scale *across* hosts, not within one.
- **BFS vs priority** — pure BFS ignores importance; the front-queue layer fixes it but adds tuning knobs.
- **Bloom filter false positives** — you may skip a real URL; acceptable trade for memory at web scale.
- **Freshness vs cost** — recrawling everything is wasteful; model per-page change rate.
- **Spider traps are endless** — combine heuristics (URL length, depth, dynamic params) + blocklists; no single fix.
- **robots.txt is honor-system** — respecting it is mandatory for a well-behaved bot; ignoring it gets you IP-banned and is unethical.
- **DNS is a hidden bottleneck** — uncached, synchronous DNS can dominate latency; dedicate a cached resolver.

---

## Common follow-up questions

- *"BFS or DFS?"* → BFS (FIFO frontier). DFS can dive arbitrarily deep into one site and is impolite; BFS gives breadth + natural politeness layering.
- *"How do you not DoS a single site?"* → one back queue per host + a worker bound to it + a min-heap enforcing a per-host delay → at most one outstanding request per host.
- *"How do you dedupe at web scale?"* → URL Seen? = Bloom filter (tiny memory, accepts rare false positives); Content Seen? = hash of page body (catches mirrors, ~30% of the web).
- *"How do you decide what to recrawl?"* → freshness model: recrawl frequency ∝ historical change rate × page importance. News homepage minutes; static doc months.
- *"How do you escape spider traps?"* → caps on URL length / crawl depth / dynamic-param count, plus blocklists and anomaly detection — no single fix.
- *"A crawler node dies — now what?"* → consistent hashing rebalances its host shard; persisted frontier + seen filters let work resume without a full restart.

---

## One-page summary

```
   GOAL: traverse the web graph from seeds, scale + polite + robust

   ALGO:    BFS over link graph (frontier = FIFO + smarts)
   FRONTIER: Mercator → front queues (priority)
                        back queues  (1 host each = politeness)
                        min-heap     (freshness / next-fetch time)
   DEDUPE:  Content Seen? (hash) + URL Seen? (Bloom filter)
   POLITE:  robots.txt + per-host delay + 1 conn/host
   PERF:    distributed (host-sharded) + DNS cache + locality + timeout
   ROBUST:  consistent hashing, persisted state, exception isolation
   TRAPS:   url-length/depth caps, blocklists, content hashing
```

## Notes
_Add your own notes here._
