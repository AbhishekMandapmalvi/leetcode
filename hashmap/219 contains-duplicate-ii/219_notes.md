# #219 — Contains Duplicate II

> **Difficulty:** Easy | **Patterns:** HashMap, Sliding Window | **Date:** 2026-04-13

**My approach:** Dict of value → last index; return True on collision within `k`, otherwise update index.

**Where I went off track:** The `else: hs[nums[i]]=i` branch is dead code — an `elif x in hs` already covered it. Also the dict grows to O(n); a sliding-set of size k is O(k) space and conceptually cleaner.

**Optimal approach:**
- Keep a window set of at most `k` elements.
- For each `x`: if `x in window` return True.
- Add `x`; if window exceeds k, remove `nums[i-k]`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">nums=[1,2,3,1], k=3 — window of size k</text>
  <g font-family="monospace" font-size="13">
    <rect x="60"  y="60" width="50" height="40" fill="#4A90D9"/><text x="85"  y="85" text-anchor="middle" fill="white">1</text>
    <rect x="115" y="60" width="50" height="40" fill="#4A90D9"/><text x="140" y="85" text-anchor="middle" fill="white">2</text>
    <rect x="170" y="60" width="50" height="40" fill="#4A90D9"/><text x="195" y="85" text-anchor="middle" fill="white">3</text>
    <rect x="225" y="60" width="50" height="40" fill="#E74C3C"/><text x="250" y="85" text-anchor="middle" fill="white">1!</text>
    <text x="350" y="85" fill="#27AE60">1 still in window of size 3 → True</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(n) → Optimal O(n) / O(k)

**Takeaway:** "Within k" is a sliding-window signal, not just a hash-map signal.
