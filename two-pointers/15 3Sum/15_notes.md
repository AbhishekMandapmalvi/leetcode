# #15 — 3Sum

> **Difficulty:** Medium | **Patterns:** Two Pointers, Sorting | **Date:** 2026-04-13

**My approach:** Sort, fix `i`, then use a hash set of seen values to find the complementary pair.

**Where I went off track:** Solution is correct but uses O(n) extra space per outer iteration for the `seen` set. The canonical approach uses two pointers on the already-sorted array — same O(n²) time but O(1) extra space and simpler dedup.

**Optimal approach:**
- Sort the array.
- For each `i`, two pointers `l=i+1`, `r=n-1`.
- If sum<0 move `l++`; if sum>0 move `r--`; if equal record and skip duplicates on both sides.
- Skip duplicate anchors (`nums[i]==nums[i-1]`) and break when `nums[i]>0`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">Sorted: [-4,-1,-1,0,1,2] — fix i=-1, two-pointer for pair</text>
  <g font-family="monospace" font-size="14">
    <rect x="40"  y="60" width="60" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="70"  y="85" text-anchor="middle">-4</text>
    <rect x="110" y="60" width="60" height="40" fill="#27AE60"/><text x="140" y="85" text-anchor="middle" fill="white">-1 (i)</text>
    <rect x="180" y="60" width="60" height="40" fill="#4A90D9"/><text x="210" y="85" text-anchor="middle" fill="white">-1 (L)</text>
    <rect x="250" y="60" width="60" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="280" y="85" text-anchor="middle">0</text>
    <rect x="320" y="60" width="60" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="350" y="85" text-anchor="middle">1</text>
    <rect x="390" y="60" width="60" height="40" fill="#4A90D9"/><text x="420" y="85" text-anchor="middle" fill="white">2 (R)</text>
  </g>
  <text x="300" y="140" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#27AE60">i + L + R = -1 + -1 + 2 = 0 ✓ → record, move both inward</text>
</svg>

**Complexity:** Mine O(n²) / O(n) → Optimal O(n²) / O(1)

**Takeaway:** Once sorted, two pointers replace a hash set — same time, less space, simpler dedup.
