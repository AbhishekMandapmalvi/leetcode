# #58 — Length of Last Word

> **Difficulty:** Easy | **Patterns:** Array, String | **Date:** 2026-04-13

**My approach:** Scan from right: skip trailing spaces, count chars until next space.

**Where I went off track:** Nothing. Good instinct to walk from the end.

**Optimal approach:**
- `i = n-1`.
- Skip while `s[i]==' '`.
- Count while `s[i] != ' '`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">"Hello World   " → skip spaces, count "World" = 5</text>
  <g font-family="monospace" font-size="14">
    <text x="200" y="90" fill="#4A90D9">H e l l o _ W o r l d _ _ _</text>
    <text x="480" y="120" fill="#E74C3C">← i</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(1) → Optimal O(n) / O(1)

**Takeaway:** Walking from the end is a small-but-real optimization when only the last something matters.
