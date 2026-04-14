# #209 — Minimum Size Subarray Sum

> **Difficulty:** Medium | **Patterns:** Sliding Window | **Date:** 2026-04-13

**My approach:** Classic sliding window — expand `r`, shrink `l` while sum ≥ target, track min length.

**Where I went off track:** Nothing. Textbook.

**Optimal approach:**
- Accumulate into `s` as `r` advances.
- While `s >= target`: record `r-l+1`, subtract `nums[l]`, `l++`.
- Return `best` or 0.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">target=7, nums=[2,3,1,2,4,3]</text>
  <g font-family="monospace" font-size="13">
    <rect x="60"  y="60" width="50" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="85" y="85" text-anchor="middle">2</text>
    <rect x="115" y="60" width="50" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="140" y="85" text-anchor="middle">3</text>
    <rect x="170" y="60" width="50" height="40" fill="#E8F4FD" stroke="#2C3E50"/><text x="195" y="85" text-anchor="middle">1</text>
    <rect x="225" y="60" width="50" height="40" fill="#4A90D9"/><text x="250" y="85" text-anchor="middle" fill="white">2</text>
    <rect x="280" y="60" width="50" height="40" fill="#4A90D9"/><text x="305" y="85" text-anchor="middle" fill="white">4</text>
    <rect x="335" y="60" width="50" height="40" fill="#27AE60"/><text x="360" y="85" text-anchor="middle" fill="white">3</text>
  </g>
  <text x="300" y="140" text-anchor="middle" font-size="13" fill="#27AE60">window [4,3] sums to 7 → min length 2</text>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** Sliding window works only when the quantity is monotone as the window grows — positive-only sums, for instance.
