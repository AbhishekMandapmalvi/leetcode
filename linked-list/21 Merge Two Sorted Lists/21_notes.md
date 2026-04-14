# #21 — Merge Two Sorted Lists

> **Difficulty:** Easy | **Patterns:** Linked List, Merge | **Date:** 2026-04-13

**My approach:** Dummy head, splice the smaller current node, attach leftover.

**Where I went off track:** Nothing. Solid.

**Optimal approach:**
- Dummy head, `tail` pointer.
- While both lists have nodes: splice the smaller one.
- Attach `l1 or l2` at the end.
- Return `dummy.next`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">L1: 1→2→4   L2: 1→3→4   →   1→1→2→3→4→4</text>
  <g font-family="monospace" font-size="13">
    <text x="60" y="70" fill="#4A90D9">take 1 (L1), take 1 (L2)</text>
    <text x="60" y="100" fill="#4A90D9">take 2 (L1), take 3 (L2)</text>
    <text x="60" y="130" fill="#27AE60">take 4 (L1), attach rest 4 (L2)</text>
  </g>
</svg>

**Complexity:** Mine O(m+n) / O(1) → Optimal O(m+n) / O(1)

**Takeaway:** Dummy head eliminates the "first node" special case in linked-list problems.
