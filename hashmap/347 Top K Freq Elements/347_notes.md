# #347 — Top K Frequent Elements

> **Difficulty:** Medium | **Patterns:** HashMap, Heap | **Date:** 2026-04-13

**My approach:** Counter + min-heap of size k.

**Where I went off track:** Nothing — heap approach is correct and interview-solid. For the tightest complexity, know the bucket-sort trick: frequencies are ≤ n, so you can index directly.

**Optimal approach (bucket sort):**
- Count frequencies.
- `buckets[f] = list of nums with frequency f`.
- Walk from highest `f` down, collect until you have k.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">nums=[1,1,1,2,2,3], k=2</text>
  <g font-family="monospace" font-size="13">
    <text x="60" y="70" fill="#4A90D9">freq: {1:3, 2:2, 3:1}</text>
    <text x="60" y="100" fill="#4A90D9">buckets: [_, [3], [2], [1]]</text>
    <text x="60" y="130" fill="#27AE60">walk from f=3: [1] → f=2: [2] → [1,2]</text>
  </g>
</svg>

**Complexity:** Mine O(n log k) / O(n) → Optimal O(n) / O(n) (bucket)

**Takeaway:** When the key (here, frequency) is bounded by n, buckets beat heaps.
