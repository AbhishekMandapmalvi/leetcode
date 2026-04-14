# #88 — Merge Sorted Array

> **Difficulty:** Easy | **Patterns:** Two Pointers, Merge | **Date:** 2026-04-13

**My approach:** Copy nums2 into the tail of nums1, then bubble neighbors into place.

**Where I went off track:** That's effectively a bubble sort of the merged region — O((m+n)²). The trick for this problem is to merge from the **back**, writing the larger value into the empty tail so you never clobber unread data.

**Optimal approach:**
- `i=m-1`, `j=n-1`, `w=m+n-1`.
- Loop while `j>=0`: write the larger of `nums1[i]` and `nums2[j]` to `nums1[w]`, decrement accordingly.
- If `i` runs out first, remaining `nums2` get copied; if `j` runs out, we're done.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">nums1=[1,2,3,_,_,_] nums2=[2,5,6] — write from tail</text>
  <g font-family="monospace" font-size="14">
    <rect x="40"  y="60" width="50" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="65"  y="85" text-anchor="middle">1</text>
    <rect x="95"  y="60" width="50" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="120" y="85" text-anchor="middle">2</text>
    <rect x="150" y="60" width="50" height="40" fill="#4A90D9"/><text x="175" y="85" text-anchor="middle" fill="white">3 (i)</text>
    <rect x="205" y="60" width="50" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="230" y="85" text-anchor="middle">_</text>
    <rect x="260" y="60" width="50" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="285" y="85" text-anchor="middle">_</text>
    <rect x="315" y="60" width="50" height="40" fill="#27AE60"/><text x="340" y="85" text-anchor="middle" fill="white">_ (w)</text>
    <text x="420" y="85" fill="#2C3E50">nums2[j]=6</text>
  </g>
  <text x="300" y="140" text-anchor="middle" font-size="13" fill="#27AE60">6 > 3 → nums1[w]=6, j--, w--</text>
</svg>

**Complexity:** Mine O((m+n)²) / O(1) → Optimal O(m+n) / O(1)

**Takeaway:** When merging into a buffer that already contains data, write from the back so you never overwrite unread elements.
