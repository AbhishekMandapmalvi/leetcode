# #122 — Best Time to Buy and Sell Stock II

> **Difficulty:** Medium | **Patterns:** Array, Greedy | **Date:** 2026-04-13

**My approach:** Sum every positive day-to-day delta.

**Where I went off track:** Nothing — this is the slick version.

**Optimal approach:**
- `sum(max(prices[i]-prices[i-1], 0) for i in range(1,n))`.
- Equivalent to the peak-valley strategy, zero bookkeeping.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">[7,1,5,3,6,4] deltas: -6,+4,-2,+3,-2 → 4+3=7</text>
  <polyline points="50,120 120,150 190,70 260,110 330,60 400,90" fill="none" stroke="#4A90D9" stroke-width="2"/>
  <g font-family="monospace" font-size="12" fill="#27AE60">
    <text x="155" y="40">+4</text>
    <text x="295" y="40">+3</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** Any upward slope decomposes into a sum of daily positive deltas.
