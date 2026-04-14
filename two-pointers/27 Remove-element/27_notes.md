# #27 — Remove Element

> **Difficulty:** Easy | **Patterns:** Two Pointers, In-place | **Date:** 2026-04-13

**My approach:** While loop with `nums.pop(i)` when match.

**Where I went off track:** `list.pop(i)` shifts every element after `i`, so the overall complexity is O(n²). The fast/slow two-pointer pattern gets it to O(n).

**Optimal approach:**
- `k=0` (slow, next write slot).
- Iterate fast pointer over the array.
- If `nums[fast] != val`, write it at `k` and `k++`.
- Return `k`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">nums=[3,2,2,3], val=3 — slow writes, fast scans</text>
  <g font-family="monospace" font-size="14">
    <rect x="120" y="60" width="60" height="40" fill="#E74C3C"/><text x="150" y="85" text-anchor="middle" fill="white">3</text>
    <rect x="190" y="60" width="60" height="40" fill="#27AE60"/><text x="220" y="85" text-anchor="middle" fill="white">2</text>
    <rect x="260" y="60" width="60" height="40" fill="#27AE60"/><text x="290" y="85" text-anchor="middle" fill="white">2</text>
    <rect x="330" y="60" width="60" height="40" fill="#E74C3C"/><text x="360" y="85" text-anchor="middle" fill="white">3</text>
  </g>
  <text x="150" y="130" text-anchor="middle" font-size="12" fill="#4A90D9">skip</text>
  <text x="220" y="130" text-anchor="middle" font-size="12" fill="#4A90D9">write k=0</text>
  <text x="290" y="130" text-anchor="middle" font-size="12" fill="#4A90D9">write k=1</text>
  <text x="360" y="130" text-anchor="middle" font-size="12" fill="#4A90D9">skip</text>
  <text x="300" y="160" text-anchor="middle" font-size="13" fill="#27AE60">return k=2</text>
</svg>

**Complexity:** Mine O(n²) / O(1) → Optimal O(n) / O(1)

**Takeaway:** Never `pop(i)` inside a loop — it's O(n) per call. Overwrite with a slow pointer instead.
