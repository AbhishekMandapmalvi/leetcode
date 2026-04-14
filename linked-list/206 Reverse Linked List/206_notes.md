# #206 — Reverse Linked List

> **Difficulty:** Easy | **Patterns:** Linked List | **Date:** 2026-04-13

**My approach:** Iterative `prev`/`curr`/`next` swap.

**Where I went off track:** Nothing. Textbook.

**Optimal approach:**
- `prev=None`, `curr=head`.
- Save `next`, flip `curr.next=prev`, advance both.
- Return `prev`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">1 → 2 → 3 → None  becomes  None ← 1 ← 2 ← 3</text>
  <g font-family="monospace" font-size="14">
    <circle cx="120" cy="90" r="22" fill="#4A90D9"/><text x="120" y="95" text-anchor="middle" fill="white">1</text>
    <circle cx="220" cy="90" r="22" fill="#4A90D9"/><text x="220" y="95" text-anchor="middle" fill="white">2</text>
    <circle cx="320" cy="90" r="22" fill="#4A90D9"/><text x="320" y="95" text-anchor="middle" fill="white">3</text>
    <path d="M 142 90 L 198 90" stroke="#E74C3C" marker-end="url(#a)"/>
    <path d="M 242 90 L 298 90" stroke="#E74C3C" marker-end="url(#a)"/>
    <defs><marker id="a" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L5,3 L0,6 Z" fill="#E74C3C"/></marker></defs>
  </g>
  <text x="300" y="150" text-anchor="middle" font-size="12" fill="#27AE60">arrows flip one at a time</text>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** The three-pointer reverse is a building block for many list problems — burn it into muscle memory.
