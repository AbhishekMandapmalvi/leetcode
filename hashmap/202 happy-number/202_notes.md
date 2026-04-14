# #202 — Happy Number

> **Difficulty:** Easy | **Patterns:** HashMap, Math | **Date:** 2026-04-13

**My approach:** Iterate `n → sum of digit squares`, track seen values in a set, stop when `n==1` or `n` seen again.

**Where I went off track:** Minor: the early `if 1 < n < 3: return False` is wrong — `n=2` is correctly unhappy but the check is confusing and accidentally relies on the cycle catching it. Remove it. Also has an off-by-one feel. The main solution is fine.

**Optimal approach:**
- Hash-set version: simple, O(k) space where k is path length.
- O(1) version: Floyd's cycle detection on the `step(n)` function.
- Either way it runs in a tiny number of steps for any input.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">19 → 1² + 9² = 82 → 68 → 100 → 1 ✓ happy</text>
  <g font-family="monospace" font-size="13">
    <rect x="40"  y="70" width="60" height="40" fill="#4A90D9"/><text x="70"  y="95" text-anchor="middle" fill="white">19</text>
    <text x="115" y="95">→</text>
    <rect x="140" y="70" width="60" height="40" fill="#4A90D9"/><text x="170" y="95" text-anchor="middle" fill="white">82</text>
    <text x="215" y="95">→</text>
    <rect x="240" y="70" width="60" height="40" fill="#4A90D9"/><text x="270" y="95" text-anchor="middle" fill="white">68</text>
    <text x="315" y="95">→</text>
    <rect x="340" y="70" width="60" height="40" fill="#4A90D9"/><text x="370" y="95" text-anchor="middle" fill="white">100</text>
    <text x="415" y="95">→</text>
    <rect x="440" y="70" width="60" height="40" fill="#27AE60"/><text x="470" y="95" text-anchor="middle" fill="white">1</text>
  </g>
</svg>

**Complexity:** Mine O(k) / O(k) → Optimal O(k) / O(1) (Floyd)

**Takeaway:** Any "iterate a function until stable or cycle" problem is a cycle-detection problem. Set is easy; Floyd is O(1) space.
