# #189 — Rotate Array

> **Difficulty:** Medium | **Patterns:** Array, In-place | **Date:** 2026-04-13

**My approach:** Slice the array into two parts and reassign via `nums[0:k]`, `nums[k:]`.

**Where I went off track:** Works but uses O(n) extra memory. The problem asks for in-place. The canonical O(1) trick is the **triple reverse**.

**Optimal approach:**
- `k %= n`.
- Reverse `nums[0..n-1]`.
- Reverse `nums[0..k-1]`.
- Reverse `nums[k..n-1]`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">[1,2,3,4,5,6,7] k=3 → [5,6,7,1,2,3,4]</text>
  <g font-family="monospace" font-size="13">
    <text x="60" y="70" fill="#4A90D9">step 1: reverse all → [7,6,5,4,3,2,1]</text>
    <text x="60" y="100" fill="#4A90D9">step 2: reverse [0..k-1] → [5,6,7,4,3,2,1]</text>
    <text x="60" y="130" fill="#27AE60">step 3: reverse [k..n-1] → [5,6,7,1,2,3,4]</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(n) → Optimal O(n) / O(1)

**Takeaway:** Triple reverse is the canonical O(1)-space rotation — memorize it.
