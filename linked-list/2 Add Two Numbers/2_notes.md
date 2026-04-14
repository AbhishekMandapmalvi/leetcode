# #2 — Add Two Numbers

> **Difficulty:** Medium | **Patterns:** Linked List | **Date:** 2026-04-13

**My approach:** Dummy head + carry, walk both lists, append one digit per iteration.

**Where I went off track:** Minor — you handle the trailing carry with a separate `if carry>0` after the loop. Cleaner is `while l1 or l2 or carry:` which folds the last carry into the main loop.

**Optimal approach:**
- Dummy head.
- `while l1 or l2 or carry`: take digits (0 if None), sum, divmod by 10, append.
- Return `dummy.next`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">342 + 465 = 807  →  [2,4,3]+[5,6,4]=[7,0,8]</text>
  <g font-family="monospace" font-size="14">
    <text x="60"  y="80" fill="#4A90D9">2+5+0 = 7, carry 0</text>
    <text x="60"  y="110" fill="#4A90D9">4+6+0 = 10, carry 1, digit 0</text>
    <text x="60"  y="140" fill="#27AE60">3+4+1 = 8, carry 0, digit 8</text>
  </g>
</svg>

**Complexity:** Mine O(max(m,n)) / O(1) → Optimal same

**Takeaway:** Fold the trailing carry into the loop condition (`or carry`).
