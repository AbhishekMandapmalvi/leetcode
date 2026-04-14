# #14 — Longest Common Prefix

> **Difficulty:** Easy | **Patterns:** Array, String | **Date:** 2026-04-13

**My approach:** Sort, then compare first and last string character by character.

**Where I went off track:** Nothing. Clever approach.

**Optimal approach:**
- Sort lexicographically.
- Compare `strs[0]` and `strs[-1]` char by char; that prefix is the answer.
- Alt: vertical scan with `zip(*strs)`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">["flower","flow","flight"] → sort → ["flight","flow","flower"]</text>
  <g font-family="monospace" font-size="14">
    <text x="100" y="80" fill="#4A90D9">flight</text>
    <text x="100" y="110" fill="#4A90D9">flower</text>
    <text x="280" y="95" fill="#27AE60">common prefix = "fl"</text>
  </g>
</svg>

**Complexity:** Mine O(n log n · k) / O(1) → vertical scan O(n·k) / O(1)

**Takeaway:** After sorting, only the extremes matter — the middle strings are bounded by them.
