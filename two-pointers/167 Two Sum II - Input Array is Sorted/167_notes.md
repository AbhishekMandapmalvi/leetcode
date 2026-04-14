# #167 — Two Sum II (Sorted)

> **Difficulty:** Medium | **Patterns:** Two Pointers | **Date:** 2026-04-13

**My approach:** Two pointers at both ends, shrink based on sum comparison.

**Where I went off track:** Nothing. Solution is textbook.

**Optimal approach:**
- `l=0`, `r=n-1`.
- If `nums[l]+nums[r] < target`: `l++`.
- If `>`: `r--`.
- If `==`: return `[l+1, r+1]`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">[2,7,11,15], target=9</text>
  <g font-family="monospace" font-size="14">
    <rect x="100" y="60" width="60" height="40" fill="#4A90D9"/><text x="130" y="85" text-anchor="middle" fill="white">2 (L)</text>
    <rect x="180" y="60" width="60" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="210" y="85" text-anchor="middle">7</text>
    <rect x="260" y="60" width="60" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="290" y="85" text-anchor="middle">11</text>
    <rect x="340" y="60" width="60" height="40" fill="#4A90D9"/><text x="370" y="85" text-anchor="middle" fill="white">15 (R)</text>
  </g>
  <text x="300" y="130" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#E74C3C">2+15=17 &gt; 9 → R--</text>
  <text x="300" y="155" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#27AE60">2+7=9 ✓ → return [1,2]</text>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** Sorted input is a signal to reach for two pointers before a hash map.
