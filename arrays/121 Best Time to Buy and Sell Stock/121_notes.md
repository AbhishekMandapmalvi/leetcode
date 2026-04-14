# #121 — Best Time to Buy and Sell Stock

> **Difficulty:** Easy | **Patterns:** Array, Greedy | **Date:** 2026-04-13

**My approach:** Track running min price and max profit in a single pass.

**Where I went off track:** Nothing. Textbook.

**Optimal approach:**
- `lo = +inf`, `best = 0`.
- For each price: `lo = min(lo, p)`; `best = max(best, p - lo)`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">[7,1,5,3,6,4] — best buy 1 sell 6 = 5</text>
  <g font-family="monospace" font-size="14">
    <rect x="50"  y="60" width="50" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="75"  y="85" text-anchor="middle">7</text>
    <rect x="105" y="60" width="50" height="40" fill="#27AE60"/><text x="130" y="85" text-anchor="middle" fill="white">1▼</text>
    <rect x="160" y="60" width="50" height="40" fill="#4A90D9"/><text x="185" y="85" text-anchor="middle" fill="white">5</text>
    <rect x="215" y="60" width="50" height="40" fill="#4A90D9"/><text x="240" y="85" text-anchor="middle" fill="white">3</text>
    <rect x="270" y="60" width="50" height="40" fill="#27AE60"/><text x="295" y="85" text-anchor="middle" fill="white">6▲</text>
    <rect x="325" y="60" width="50" height="40" fill="#4A90D9"/><text x="350" y="85" text-anchor="middle" fill="white">4</text>
  </g>
  <text x="300" y="140" text-anchor="middle" font-size="13" fill="#27AE60">profit = 6 - 1 = 5</text>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** "Best X so far" patterns run in one pass with two tracking variables.
