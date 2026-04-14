# #205 — Isomorphic Strings

> **Difficulty:** Easy | **Patterns:** HashMap, String | **Date:** 2026-04-13

**My approach:** Two maps `s→t` and `t→s`, enforce consistency on every pair.

**Where I went off track:** Nothing. Solution is correct.

**Optimal approach:**
- Two dicts to enforce a bijection.
- For each `(a,b)` in `zip(s,t)`: check either existing mapping is consistent, else add both.
- Reject on any contradiction.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">s="egg" t="add" → e↔a, g↔d ✓</text>
  <g font-family="monospace" font-size="14">
    <text x="100" y="80" fill="#4A90D9">e → a</text>
    <text x="100" y="110" fill="#4A90D9">g → d</text>
    <text x="100" y="140" fill="#4A90D9">g → d ✓</text>
    <text x="350" y="80" fill="#E74C3C">s="foo" t="bar" → o→a ✗ (o already → r)</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** "Bijection" problems need two maps, not one.
