# Chapter 2: Back-Of-The-Envelope Estimation

Use thought experiments and common performance numbers to make rough capacity and performance estimates during system design interviews. The goal is **directional accuracy**, not precision — you're proving you can reason about scale, not running a benchmark.

> Jeff Dean (Google): "Back-of-the-envelope calculations are estimates you create using a combination of thought experiments and common performance numbers to get a good feel for which designs will meet your requirements."

---

## Key Topics

### Power of two (data volume units)
Storage and memory are quoted in powers of 2. Memorize these — they appear in almost every storage estimate.

| Power | Approx Value | Name        | Short |
| ----- | ------------ | ----------- | ----- |
| 2^10  | 1 thousand   | 1 Kilobyte  | KB    |
| 2^20  | 1 million    | 1 Megabyte  | MB    |
| 2^30  | 1 billion    | 1 Gigabyte  | GB    |
| 2^40  | 1 trillion   | 1 Terabyte  | TB    |
| 2^50  | 1 quadrillion| 1 Petabyte  | PB    |

```
   1 byte = 8 bits   ASCII char = 1 byte
   1 KB ≈ 10^3 B   ──►   short text
   1 MB ≈ 10^6 B   ──►   small image / short song
   1 GB ≈ 10^9 B   ──►   movie
   1 TB ≈ 10^12 B  ──►   large DB
   1 PB ≈ 10^15 B  ──►   YouTube/FB-scale storage
```

**Char encoding sanity check**
- ASCII char = 1 byte
- Unicode char (UTF-8): 1–4 bytes
- A `long` = 8 bytes
- Tweet (280 chars) ≈ 280 bytes (ASCII) or up to ~1 KB (UTF-8)

---

### Latency numbers every programmer should know
Originally from Jeff Dean (Google, 2010 — still useful as orders of magnitude):

| Operation                                     | Time            |
| --------------------------------------------- | --------------- |
| L1 cache reference                            | 0.5 ns          |
| Branch mispredict                             | 5 ns            |
| L2 cache reference                            | 7 ns            |
| Mutex lock/unlock                             | 100 ns          |
| Main memory reference                         | 100 ns          |
| Compress 1 KB w/ Zippy                        | 10,000 ns (10 µs)  |
| Send 2 KB over 1 Gbps network                 | 20,000 ns (20 µs)  |
| Read 1 MB sequentially from memory            | 250,000 ns (250 µs) |
| Round trip within same datacenter             | 500,000 ns (0.5 ms) |
| Read 1 MB sequentially from SSD               | 1 ms            |
| Disk seek                                     | 10 ms           |
| Read 1 MB sequentially from disk              | 30 ms           |
| Send packet CA → Netherlands → CA             | 150 ms          |

```
   ns ──── µs ──── ms ──── s
   L1   network   disk   ─►  user-visible
   100M faster than disk;  disk 30× faster than cross-continent RTT
```

**Takeaways for design**
- **Memory is fast, disk is slow** — cache hot data in memory.
- **Avoid disk seeks** — sequential I/O is dramatically faster than random.
- **Compression is cheap** (10 µs per KB) — compress before network if WAN-bound.
- **Cross-region calls are expensive** (~150 ms) — keep the request path in one region; replicate data across regions in the background.
- **Same-DC RTT ≈ 0.5 ms** — many such hops in one user request adds up; mind the request fan-out.

---

### Availability numbers (the "nines")
SLA/SLO targets expressed as the percentage of time the service is up. Most cloud providers offer 99.9–99.99%.

| Availability | Downtime / day | Downtime / year |
| ------------ | -------------- | --------------- |
| 99%          | 14.40 min      | 3.65 days       |
| 99.9%        | 1.44 min       | 8.77 hours      |
| 99.99%       | 8.64 sec       | 52.60 min       |
| 99.999%      | 864 ms         | 5.26 min        |
| 99.9999%     | 86.4 ms        | 31.56 sec       |

```
   3 nines  →  ~9 hr/year     OK for many internal tools
   4 nines  →  ~53 min/year   typical SaaS target
   5 nines  →  ~5 min/year    telco / payments grade
```

Each extra "9" usually means another redundancy layer, multi-AZ/multi-region, automated failover, and far more ops investment.

---

### Estimating QPS, storage, bandwidth, memory
**General method**
1. Start from **DAU** (daily active users).
2. Pick a **per-user action rate** (tweets/day, posts/day, requests/session).
3. Convert to **per-second** using `seconds/day ≈ 86,400 ≈ 100K` (round up).
4. Multiply by per-action size for **bandwidth/storage**.
5. Apply **read:write ratio** (often 100:1 or higher for social/feed apps).
6. Add a **peak factor** (peak QPS ≈ 2–3× average).

```
   DAU ─► actions/user/day ─► QPS = (DAU × actions) / 86,400
                              peak QPS ≈ 2–3 × QPS
                              storage = QPS × payload_size × seconds × retention
                              bandwidth = QPS × payload_size
```

**Rounding rules of thumb**
- Use `100K` for seconds-per-day.
- Use `300M` for "social-scale DAU".
- Use `10^9` for a billion.
- Round to one significant digit; the answer is approximate anyway.

---

### Example: Twitter QPS and storage estimation
Assumptions
- 300 million MAU
- 50% are DAU → **150M DAU**
- Each user posts **2 tweets/day on average**
- 10% of tweets contain media
- Tweet retention: **5 years**

**Tweet QPS**
```
   tweets/day = 150M × 2          = 300M tweets/day
   QPS        = 300M / 86,400     ≈ 3,500 tweets/sec
   peak QPS   ≈ 2 × QPS           ≈ 7,000 tweets/sec
```

**Media QPS**
```
   media tweets/sec = 10% × 3,500 ≈ 350 media-tweets/sec
```

**Storage (per tweet)**
```
   tweet_id      :    64 bytes
   text          :   140 bytes
   media         :  ~1 MB (avg, only 10% of tweets)

   per-tweet avg storage
     text-only 90%:  204 B   ≈ negligible vs media
     media 10%   : ~1 MB

   daily new media = 300M × 10% × 1 MB ≈ 30 TB / day
   5-year media    = 30 TB × 365 × 5    ≈ 55 PB
```

```
   ┌──────── inputs ────────┐    ┌─── derived ───┐
   │ 300M MAU               │    │  150M DAU     │
   │ 2 tweets/user/day      │ ─► │  3.5K QPS     │
   │ 10% have media         │    │  7K peak QPS  │
   │ retention 5 yr         │    │  ~55 PB media │
   └────────────────────────┘    └───────────────┘
```

---

### Tips: rounding, assumptions, labeling units
- **State assumptions out loud** ("I'm assuming 50% of MAU are DAU"). The interviewer will correct you if it matters.
- **Round aggressively** — `86,400 → 100K`, `365 → 400`. Off by 20%, fine for sizing.
- **Always label units** — `7K tweets/sec`, `55 PB`, never bare numbers.
- **One significant digit** is enough; precision implies false confidence.
- **Sanity-check the answer** — does "5 PB/day" feel right? Cross-check against known scale (YouTube ingests ~PB/day).
- **Separate average from peak** — design must handle peak; cost is driven by average.
- **Read vs write ratio matters** — design and storage often care about reads (timeline = 100s of fanouts per write).
- **Show the worksheet** — interviewers care about the method, not the final number.

---

## Quick reference cheat sheet
```
   1 day            = 86,400 s     ≈ 100K s
   1 year           ≈ 365 days     ≈ 400 days (rounded up)
   ASCII char       = 1 byte
   long / int64     = 8 bytes
   UUID             = 16 bytes
   tweet text       ≈ 280 bytes
   typical image    ≈ 200 KB
   typical video min≈ 50 MB

   QPS  = events/day  ÷ 100K
   peak ≈ 2-3 × QPS
   storage/yr = QPS × size × 32M  (≈ seconds in a year)
```

## Notes
_Add your own notes here._
