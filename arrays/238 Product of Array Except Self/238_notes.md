# #238 — Product of Array Except Self

> **Difficulty:** Medium | **Patterns:** Array, Prefix Sum | **Date:** 2026-04-13

**My approach:** Left-pass fills `out[i]=prefix`, right-pass multiplies in `suffix`.

**Where I went off track:** Nothing. Textbook.

**Optimal approach:**
- Left pass: `out[i] = product of nums[0..i-1]`.
- Right pass: `out[i] *= product of nums[i+1..n-1]`.
- Output array isn't counted as extra space.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">nums=[1,2,3,4]</text>
  <g font-family="monospace" font-size="14">
    <text x="60" y="70" fill="#4A90D9">left pass:  [1, 1, 2, 6]</text>
    <text x="60" y="100" fill="#4A90D9">right pass: ×24, ×12, ×4, ×1</text>
    <text x="60" y="130" fill="#27AE60">result:     [24, 12, 8, 6]</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** Prefix + suffix scan is the go-to for "exclude self" problems without division.
