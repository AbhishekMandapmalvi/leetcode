# #228 — Summary Ranges

> **Difficulty:** Easy | **Patterns:** Array, Intervals | **Date:** 2026-04-13

**My approach:** Walk, extend consecutive runs, emit `start` or `start->end`.

**Where I went off track:** Nothing.

**Optimal approach:**
- Track `start`. Advance while `nums[i+1]==nums[i]+1`.
- Emit singleton or range.
- `i += 1` to move past the run.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">[0,1,2,4,5,7] → ["0->2","4->5","7"]</text>
  <g font-family="monospace" font-size="14">
    <rect x="60" y="60" width="50" height="40" fill="#4A90D9"/><text x="85" y="85" text-anchor="middle" fill="white">0</text>
    <rect x="115" y="60" width="50" height="40" fill="#4A90D9"/><text x="140" y="85" text-anchor="middle" fill="white">1</text>
    <rect x="170" y="60" width="50" height="40" fill="#4A90D9"/><text x="195" y="85" text-anchor="middle" fill="white">2</text>
    <rect x="240" y="60" width="50" height="40" fill="#27AE60"/><text x="265" y="85" text-anchor="middle" fill="white">4</text>
    <rect x="295" y="60" width="50" height="40" fill="#27AE60"/><text x="320" y="85" text-anchor="middle" fill="white">5</text>
    <rect x="365" y="60" width="50" height="40" fill="#E74C3C"/><text x="390" y="85" text-anchor="middle" fill="white">7</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** "Detect consecutive runs" is a one-pass loop-within-loop — the inner loop doesn't break amortized O(n).
