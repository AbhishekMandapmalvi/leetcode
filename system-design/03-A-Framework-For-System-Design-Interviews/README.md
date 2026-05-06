# Chapter 3: A Framework For System Design Interviews

A system design interview is **not** about producing a perfect blueprint. It is a **collaborative conversation** that simulates real-world problem solving with vague requirements and incomplete info. The interviewer is judging:

- Your **design skills** and how you defend trade-offs.
- Your **collaboration** — do you ask, listen, adapt?
- Your **handling of ambiguity** under pressure.
- **Red flags:** narrow-minded, inflexible, over-engineering, stubborn refusal to consider alternatives.

The book gives a 4-step framework that fits any 45-minute interview.

```
   ┌──────────────────────────────────────────────────────────┐
   │  Step 1     Step 2          Step 3            Step 4     │
   │  ──────     ──────          ──────            ──────     │
   │  Scope &    High-level      Deep dive         Wrap up    │
   │  reqs       design          (1-2 areas)                  │
   │  3-10 min   10-15 min       10-25 min         3-5 min    │
   └──────────────────────────────────────────────────────────┘
```

---

## Step 1: Understand the problem and establish design scope (3–10 min)

> "The most important skill is asking the right questions, making the right assumptions, and gathering all the information needed to build a system."

### Goal
Don't dive into a solution. Define **what** you're building, **for whom**, and **at what scale**, before drawing a single box.

### Categories of questions to ask
1. **Features / use cases** — what exactly does the system do? Which features are in scope, which are out?
2. **Users / scale** — DAU, MAU, growth rate, geographic distribution.
3. **Read/write ratio** — heavy reads, heavy writes, or balanced?
4. **Data** — what data, how big, how long retained?
5. **Performance / SLAs** — latency targets, availability goals, consistency needs.
6. **Non-functional** — security, privacy/regulatory, internationalization, mobile vs web.
7. **Existing constraints** — anything to integrate with? Tech stack constraints?

### Example (Designing a news feed system from the book)
- *Mobile, web, or both?* Both.
- *Most important features?* Post + view friends' news feed.
- *Sorting?* Reverse chronological for now.
- *How many friends per user?* Up to 5,000.
- *Traffic?* 10M DAU.
- *Can feed contain media?* Yes — images and videos.

```
   Vague brief        ──►   Clarifying Qs   ──►   Concrete spec
   "design news feed"        features?              ┌─────────────┐
                             scale?                 │ 10M DAU     │
                             reads vs writes?       │ 5K friends  │
                             media?                 │ images/video│
                                                    │ chrono sort │
                                                    └─────────────┘
```

### State your assumptions
If the interviewer is silent, **state assumptions explicitly** ("I'll assume 100M DAU and a 100:1 read:write ratio") and continue. The interviewer will correct you if needed.

---

## Step 2: Propose high-level design and get buy-in (10–15 min)

### Goal
Sketch a **first-pass architecture** with the major boxes, name the APIs, and walk the interviewer through the **happy-path data flow**. This is a discussion, not a monologue.

### What to produce
1. **Box-and-arrow diagram** — clients, LB, web/app servers, cache, DB, queue, workers, CDN, etc.
2. **Public APIs** — endpoint, params, response. (REST endpoints, gRPC methods, etc.)
3. **Data model sketch** — tables/collections and their key columns.
4. **Walk through 1–2 critical flows** end-to-end (e.g. *post a tweet*, *load the feed*).
5. **Back-of-the-envelope numbers** if scale matters (Chapter 2).

```
                      ┌──────────────────────┐
                      │  HIGH-LEVEL DIAGRAM  │
                      └──────────────────────┘

      Client ──► LB ──► Web/App ──► Cache ──► DB
                              │
                              └──► Queue ──► Workers
```

### Interaction tips
- Pause and ask: *"Does this look right?"* / *"Anything you'd like me to adjust?"*
- Treat it as a **whiteboard conversation**, not a presentation. The interviewer's pushback is information, not failure.
- Keep the first pass **simple** — you'll deepen it in step 3.
- If the scale is huge, **sketch the simple version first**, then explicitly call out where it will break.

---

## Step 3: Design deep dive (10–25 min)

### Goal
Both of you should already agree on the high-level design. Now pick **1–2 components** and go deep, driven by what's most interesting/critical (the interviewer often steers).

### What "deep dive" looks like
- Justify the **storage choice** (SQL vs NoSQL, why this DB, sharding key, indexes).
- Walk through **algorithms** (consistent hashing, rate-limiting algo, ranking, fan-out strategy).
- Address **bottlenecks and scaling** — where does it break first, and how do you scale that piece?
- Address **failure modes** — what if the cache dies? a DC fails? a worker crashes mid-task?
- Discuss **trade-offs explicitly** (latency vs consistency, push vs pull, sync vs async).

### Examples of deep-dive areas per system
| System         | Likely deep dives                                  |
| -------------- | -------------------------------------------------- |
| URL shortener  | hash function, base62, collision handling, DB schema |
| Chat system    | WebSocket session mgmt, presence, message ordering |
| News feed      | fanout-on-write vs read, hybrid for celebrities    |
| Rate limiter   | token bucket vs sliding window, Redis atomicity    |
| Search autocomplete | trie + top-k, real-time vs batch updates      |

### Communicating trade-offs
There is no "correct" answer — there is the **answer you can defend**. Always say:
- *"Option A vs B…"*
- *"I'd choose A here because **X is more important than Y in our requirements**."*

```
   Constraint: low latency, eventual consistency OK
                    │
                    ▼
        Pick AP system (Cassandra/Dynamo) ──► defend with CAP
        Discuss replication factor, quorum (R/W), conflict resolution
```

### Time discipline
Don't get stuck deepening one component for 25 minutes. Aim for **breadth-then-depth** so you don't run out of time before showing your range.

---

## Step 4: Wrap up (3–5 min)

### Goal
Close the loop. Show that you understand the system as a whole, not just the parts you drew.

### What to cover
1. **Recap** the design in one minute — main components, key flows.
2. Identify **bottlenecks** the interviewer didn't ask about and how to fix them.
3. Propose **future improvements** if you had more time:
   - Sharding strategy refinements
   - Multi-region / HA upgrades
   - Caching layers
   - Better monitoring / alerting (logging, metrics)
   - Security hardening (auth, rate limit, encryption)
   - Edge cases not yet handled
4. Mention **error/edge cases**: server failures, network partitions, data loss, stale cache, retries, idempotency.
5. **Operational concerns**: monitoring, on-call, deploy strategy, capacity planning.

```
   Wrap-up checklist
   ─────────────────
   [ ] Recap design (1 min)
   [ ] Bottlenecks
   [ ] Failure modes & recovery
   [ ] Future improvements
   [ ] Open questions (if any)
```

---

## Dos and don'ts during the interview

### Do
- ✅ **Ask clarifying questions.** Don't assume; confirm.
- ✅ **State assumptions** explicitly when the interviewer is silent.
- ✅ **Think out loud** — they're scoring your reasoning, not just the artifact.
- ✅ **Suggest multiple approaches**, then pick one with justification.
- ✅ **Engage** with hints — interviewers steer because they want you to do well.
- ✅ Discuss **trade-offs**, not "the right answer".
- ✅ Cover **non-functional requirements** (scalability, availability, consistency).
- ✅ **Time-box** yourself — keep moving.

### Don't
- ❌ Jump straight to a solution before understanding the problem.
- ❌ Stay silent — the interviewer can't grade what they can't hear.
- ❌ Be over-attached to one technology / pattern.
- ❌ Defend your design when the interviewer is signalling a gap; **adapt**.
- ❌ Over-engineer (premature sharding/microservices) when not justified by scale.
- ❌ Use buzzwords without substance — only mention Kafka / Cassandra / Kubernetes if you can defend why.
- ❌ Ignore monitoring, security, error handling — interviewers notice.
- ❌ Get stuck on one section while the clock runs out.

---

## Time allocation (45-minute interview)

```
   Step                              Time     Cumulative
   ──────────────────────────────    ─────    ──────────
   1. Scope & requirements           3-10 min     ~10 min
   2. High-level design              10-15 min    ~25 min
   3. Deep dive                      10-25 min    ~40 min
   4. Wrap up                        3-5 min      ~45 min
```

**Adjust on the fly** — if the interviewer drives you deep early, follow them. If they're silent in step 2, ask questions to keep dialogue alive.

---

## One-page mental model

```
   ┌─────────────────────────────────────────────────────┐
   │  ASK   →   SKETCH   →   DEEP DIVE   →   WRAP UP     │
   │  ───       ──────       ─────────       ───────     │
   │  what?     boxes        bottlenecks     recap       │
   │  scale?    flow         trade-offs      future work │
   │  who for?  APIs         failure modes   edge cases  │
   │  reads vs  data model   scaling story                │
   │  writes?                                             │
   └─────────────────────────────────────────────────────┘
```

## Notes
_Add your own notes here._
