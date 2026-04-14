# #11 — Container With Most Water

> **Difficulty:** Medium | **Patterns:** Two Pointers | **Date:** 2026-04-13

**My approach:** Two pointers at both ends, track max area, move the shorter wall inward.

**Where I went off track:** Nothing major. Minor: used `height[start] <= height[end]` — the `=` case is harmless but unnecessary.

**Optimal approach:**
- Start `l=0`, `r=n-1`.
- Area = `(r-l) * min(h[l], h[r])`.
- Always move the pointer at the shorter wall — the taller side can't help when width shrinks.
- Stop when `l >= r`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">Two-Pointer Sweep on heights [1,8,6,2,5,4,8,3,7]</text>
  <g font-family="sans-serif" font-size="12" fill="#2C3E50">
    <rect x="40"  y="120" width="40" height="20" fill="#4A90D9"/><text x="60"  y="135" text-anchor="middle" fill="white">1</text>
    <rect x="90"  y="40"  width="40" height="100" fill="#E8F4FD" stroke="#2C3E50"/><text x="110" y="95" text-anchor="middle">8</text>
    <rect x="140" y="60"  width="40" height="80" fill="#E8F4FD" stroke="#2C3E50"/><text x="160" y="105" text-anchor="middle">6</text>
    <rect x="190" y="100" width="40" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="210" y="125" text-anchor="middle">2</text>
    <rect x="240" y="70"  width="40" height="70" fill="#E8F4FD" stroke="#2C3E50"/><text x="260" y="110" text-anchor="middle">5</text>
    <rect x="290" y="80"  width="40" height="60" fill="#E8F4FD" stroke="#2C3E50"/><text x="310" y="115" text-anchor="middle">4</text>
    <rect x="340" y="40"  width="40" height="100" fill="#E8F4FD" stroke="#2C3E50"/><text x="360" y="95" text-anchor="middle">8</text>
    <rect x="390" y="90"  width="40" height="50" fill="#E8F4FD" stroke="#2C3E50"/><text x="410" y="120" text-anchor="middle">3</text>
    <rect x="440" y="50"  width="40" height="90" fill="#4A90D9"/><text x="460" y="100" text-anchor="middle" fill="white">7</text>
    <text x="60"  y="160" text-anchor="middle" fill="#4A90D9">L</text>
    <text x="460" y="160" text-anchor="middle" fill="#4A90D9">R</text>
    <text x="260" y="30" text-anchor="middle" fill="#27AE60">best so far: width×min(L,R)</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** When a metric is bounded by the smaller of two endpoints, moving that endpoint is always the right greedy choice.
