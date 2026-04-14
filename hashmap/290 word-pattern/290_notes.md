# #290 — Word Pattern

> **Difficulty:** Easy | **Patterns:** HashMap, String | **Date:** 2026-04-13

**My approach:** Two dicts `char→word` and `word→char`, enforce consistency per pair.

**Where I went off track:** Nothing. Identical structure to LC 205 Isomorphic Strings — you already see the pattern.

**Optimal approach:**
- Split `s` into words, check length.
- `zip(pattern, words)`: maintain two maps; reject on contradiction.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">pattern="abba" s="dog cat cat dog"</text>
  <g font-family="monospace" font-size="13">
    <text x="60" y="70" fill="#4A90D9">a ↔ dog</text>
    <text x="60" y="100" fill="#4A90D9">b ↔ cat</text>
    <text x="60" y="130" fill="#27AE60">check "abba" against "dog cat cat dog" → True</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(n) → Optimal O(n) / O(n)

**Takeaway:** Word Pattern == Isomorphic Strings on tokens — one template handles both.
