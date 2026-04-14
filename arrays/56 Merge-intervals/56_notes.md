# #56 — Merge Intervals

> **Difficulty:** Medium | **Patterns:** Array, Intervals, Sorting | **Date:** 2026-04-13

**My approach:** Sort, then handle three cases (extend, swallow, append).

**Where I went off track:** Minor — you split overlap into two branches ("extend" vs "fully contained"). The cleaner form is one check: `if start <= last_end: last_end = max(last_end, end)`.

**Optimal approach:**
- Sort by start.
- For each interval, if it overlaps the last result interval, extend its end to `max(...)`; otherwise append.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">[[1,3],[2,6],[8,10],[15,18]] → [[1,6],[8,10],[15,18]]</text>
  <g>
    <line x1="60" y1="80" x2="180" y2="80" stroke="#4A90D9" stroke-width="6"/>
    <line x1="120" y1="100" x2="300" y2="100" stroke="#4A90D9" stroke-width="6"/>
    <line x1="340" y1="120" x2="420" y2="120" stroke="#27AE60" stroke-width="6"/>
    <line x1="460" y1="140" x2="540" y2="140" stroke="#27AE60" stroke-width="6"/>
  </g>
  <text x="300" y="170" text-anchor="middle" font-size="12" fill="#27AE60">merged [1,6] covers the first two</text>
</svg>

**Complexity:** Mine O(n log n) / O(n) → Optimal same

**Takeaway:** Sort-first + one-line overlap extension. Don't split into multiple overlap cases.
