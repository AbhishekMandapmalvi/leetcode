# #55 — Jump Game

> **Difficulty:** Medium | **Patterns:** Greedy, Array | **Date:** 2026-04-13

**My approach:** Walk backward: if `i + nums[i] >= last`, shrink `last = i`. Return `last == 0`.

**Where I went off track:** Nothing. Backward greedy is correct and elegant. Forward greedy (`farthest`) is the more common template and a bit simpler to reason about.

**Optimal approach (forward):**
- Track `farthest = 0`.
- At each `i`, if `i > farthest`: return False.
- Else `farthest = max(farthest, i + nums[i])`.
- Return True.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">[2,3,1,1,4] → farthest expands 0→2→4→4→4</text>
  <g font-family="monospace" font-size="14">
    <rect x="80"  y="70" width="50" height="40" fill="#4A90D9"/><text x="105" y="95" text-anchor="middle" fill="white">2</text>
    <rect x="135" y="70" width="50" height="40" fill="#4A90D9"/><text x="160" y="95" text-anchor="middle" fill="white">3</text>
    <rect x="190" y="70" width="50" height="40" fill="#4A90D9"/><text x="215" y="95" text-anchor="middle" fill="white">1</text>
    <rect x="245" y="70" width="50" height="40" fill="#4A90D9"/><text x="270" y="95" text-anchor="middle" fill="white">1</text>
    <rect x="300" y="70" width="50" height="40" fill="#27AE60"/><text x="325" y="95" text-anchor="middle" fill="white">4</text>
  </g>
  <text x="300" y="140" text-anchor="middle" font-size="13" fill="#27AE60">reach end ✓</text>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal same

**Takeaway:** Forward or backward greedy both work — pick the one whose invariant is easier to state.
