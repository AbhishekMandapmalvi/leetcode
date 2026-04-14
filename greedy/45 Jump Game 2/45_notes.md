# #45 — Jump Game II

> **Difficulty:** Medium | **Patterns:** Greedy, Array | **Date:** 2026-04-13

**My approach:** BFS-in-layers greedy — track `end` of current layer and `farthest` you can reach; commit a jump when `i==end`.

**Where I went off track:** Nothing. Optimal.

**Optimal approach:**
- Iterate to `n-2` (last index doesn't need another jump).
- Update `farthest = max(farthest, i+nums[i])`.
- At `i==end`: `jumps++`, `end = farthest`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">nums=[2,3,1,1,4] → 2 jumps</text>
  <g font-family="monospace" font-size="14">
    <rect x="80"  y="70" width="60" height="40" fill="#4A90D9"/><text x="110" y="95" text-anchor="middle" fill="white">2</text>
    <rect x="150" y="70" width="60" height="40" fill="#27AE60"/><text x="180" y="95" text-anchor="middle" fill="white">3</text>
    <rect x="220" y="70" width="60" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="250" y="95" text-anchor="middle">1</text>
    <rect x="290" y="70" width="60" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="320" y="95" text-anchor="middle">1</text>
    <rect x="360" y="70" width="60" height="40" fill="#27AE60"/><text x="390" y="95" text-anchor="middle" fill="white">4</text>
  </g>
  <text x="300" y="150" text-anchor="middle" font-size="13" fill="#27AE60">jump 2→3, then 3→4 (2 jumps)</text>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal same

**Takeaway:** Jump Game II is BFS with amortized-O(1) layer tracking — no queue needed.
