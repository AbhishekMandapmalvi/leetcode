# #141 — Linked List Cycle

> **Difficulty:** Easy | **Patterns:** Linked List, Two Pointers | **Date:** 2026-04-13

**My approach:** Floyd's tortoise and hare.

**Where I went off track:** Nothing. Classic.

**Optimal approach:**
- `slow` steps by 1, `fast` by 2.
- If they ever meet, there's a cycle.
- If `fast` hits `None`, no cycle.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">slow/fast meet inside the cycle</text>
  <g font-family="monospace" font-size="13">
    <circle cx="80" cy="90" r="18" fill="#4A90D9"/><text x="80" y="95" text-anchor="middle" fill="white">1</text>
    <circle cx="150" cy="90" r="18" fill="#4A90D9"/><text x="150" y="95" text-anchor="middle" fill="white">2</text>
    <circle cx="220" cy="90" r="18" fill="#4A90D9"/><text x="220" y="95" text-anchor="middle" fill="white">3</text>
    <circle cx="290" cy="90" r="18" fill="#27AE60"/><text x="290" y="95" text-anchor="middle" fill="white">4</text>
    <circle cx="360" cy="90" r="18" fill="#4A90D9"/><text x="360" y="95" text-anchor="middle" fill="white">5</text>
    <path d="M 378 90 Q 420 50 320 50 Q 260 50 272 72" stroke="#E74C3C" fill="none" stroke-width="2"/>
  </g>
  <text x="300" y="160" text-anchor="middle" font-size="12" fill="#27AE60">fast laps slow → meet ✓</text>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** Any "cycle in linked structure" problem: reach for Floyd.
