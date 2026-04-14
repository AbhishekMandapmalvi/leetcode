# #217 — Contains Duplicate

> **Difficulty:** Easy | **Patterns:** HashMap | **Date:** 2026-04-13

**My approach:** Dict counting + dead-code `unique_set = set(nums)` that's never used.

**Where I went off track:** Built a set you never read. The whole thing is `return len(set(nums)) != len(nums)` — or early-exit with a running set.

**Optimal approach:**
- One-liner: `len(set(nums)) != len(nums)`.
- Or loop with a set and return `True` on first collision (better on dup-heavy inputs).

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">[1,2,3,1] → set={1,2,3} size 3 &lt; 4 → True</text>
  <g font-family="monospace" font-size="14">
    <rect x="100" y="70" width="60" height="40" fill="#4A90D9"/><text x="130" y="95" text-anchor="middle" fill="white">1</text>
    <rect x="170" y="70" width="60" height="40" fill="#4A90D9"/><text x="200" y="95" text-anchor="middle" fill="white">2</text>
    <rect x="240" y="70" width="60" height="40" fill="#4A90D9"/><text x="270" y="95" text-anchor="middle" fill="white">3</text>
    <rect x="310" y="70" width="60" height="40" fill="#E74C3C"/><text x="340" y="95" text-anchor="middle" fill="white">1!</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(n) → Optimal O(n) / O(n)

**Takeaway:** Delete dead code. If you don't read a variable, remove it.
