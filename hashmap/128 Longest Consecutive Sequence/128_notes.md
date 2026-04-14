# #128 — Longest Consecutive Sequence

> **Difficulty:** Medium | **Patterns:** HashMap | **Date:** 2026-04-13

**My approach:** Boundary-extension hash map — store a length at each number and patch the endpoints of the merged run.

**Where I went off track:** Your solution works but is the hardest version to reason about (easy to forget patching both endpoints). The canonical approach is simpler: hash set + only count from run heads.

**Optimal approach:**
- Put nums in a set.
- Iterate the set. If `x-1` is present, skip (not a head).
- Otherwise walk `x, x+1, x+2, ...` and measure the run.
- Track max length.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">nums=[100,4,200,1,3,2] — heads only</text>
  <g font-family="monospace" font-size="13">
    <rect x="40"  y="60" width="60" height="40" fill="#27AE60"/><text x="70"  y="85" text-anchor="middle" fill="white">1★</text>
    <rect x="110" y="60" width="60" height="40" fill="#4A90D9"/><text x="140" y="85" text-anchor="middle" fill="white">2</text>
    <rect x="180" y="60" width="60" height="40" fill="#4A90D9"/><text x="210" y="85" text-anchor="middle" fill="white">3</text>
    <rect x="250" y="60" width="60" height="40" fill="#4A90D9"/><text x="280" y="85" text-anchor="middle" fill="white">4</text>
    <text x="340" y="85" fill="#E74C3C">(2,3,4 not heads)</text>
    <rect x="470" y="60" width="60" height="40" fill="#27AE60"/><text x="500" y="85" text-anchor="middle" fill="white">100★</text>
  </g>
  <text x="300" y="140" text-anchor="middle" font-size="13" fill="#27AE60">head 1 → run 1,2,3,4 = length 4</text>
</svg>

**Complexity:** Mine O(n) / O(n) → Optimal O(n) / O(n)

**Takeaway:** "Only count from run heads" is the trick that makes the nested while loop amortized O(n).
