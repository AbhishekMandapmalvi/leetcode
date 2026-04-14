# #36 — Valid Sudoku

> **Difficulty:** Medium | **Patterns:** HashMap, Matrix | **Date:** 2026-04-13

**My approach:** 9 row sets + 9 col sets + 9 box sets, one cell at a time.

**Where I went off track:** Nothing. Clean solution.

**Optimal approach:**
- `box = (r//3)*3 + (c//3)`.
- For each filled cell, check membership in all three sets before adding.
- Any collision → invalid.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">Cell (r,c) checks rows[r], cols[c], boxes[(r//3)*3+c//3]</text>
  <g stroke="#2C3E50" fill="#E8F4FD">
    <rect x="150" y="40" width="90" height="90"/>
    <rect x="240" y="40" width="90" height="90"/>
    <rect x="330" y="40" width="90" height="90"/>
  </g>
  <g font-family="sans-serif" font-size="12" fill="#4A90D9">
    <text x="195" y="85" text-anchor="middle">box 0</text>
    <text x="285" y="85" text-anchor="middle">box 1</text>
    <text x="375" y="85" text-anchor="middle">box 2</text>
  </g>
  <text x="285" y="160" text-anchor="middle" font-size="12" fill="#27AE60">three set lookups per cell, fixed 81 cells</text>
</svg>

**Complexity:** Mine O(1) / O(1) → Optimal O(1) / O(1) (fixed board)

**Takeaway:** `(r//3)*3 + c//3` is the standard sub-grid index — memorize it.
