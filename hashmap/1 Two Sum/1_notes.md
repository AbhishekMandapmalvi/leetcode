# #1 — Two Sum

> **Difficulty:** Easy | **Patterns:** HashMap | **Date:** 2026-04-13

**My approach:** One-pass hash map — for each `num`, check if `target-num` was seen.

**Where I went off track:** Nothing. Textbook solution.

**Optimal approach:**
- Walk the array with `enumerate`.
- For each `x`, if `target-x` is in the map, return both indices.
- Otherwise insert `x → i`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">nums=[2,7,11,15], target=9</text>
  <g font-family="monospace" font-size="13">
    <text x="60"  y="60" fill="#4A90D9">i=0 x=2 → need 7, not seen → map={2:0}</text>
    <text x="60"  y="90" fill="#27AE60">i=1 x=7 → need 2, found at 0 → return [0,1]</text>
  </g>
  <rect x="60"  y="120" width="80" height="30" fill="#E8F4FD" stroke="#2C3E50"/><text x="100" y="140" text-anchor="middle" font-family="monospace" font-size="13">2→0</text>
  <rect x="150" y="120" width="80" height="30" fill="#27AE60"/><text x="190" y="140" text-anchor="middle" font-family="monospace" font-size="13" fill="white">hit!</text>
</svg>

**Complexity:** Mine O(n) / O(n) → Optimal O(n) / O(n)

**Takeaway:** Check-before-insert in a hash map is the canonical "find complement" pattern.
