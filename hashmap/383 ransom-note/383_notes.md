# #383 — Ransom Note

> **Difficulty:** Easy | **Patterns:** HashMap, String | **Date:** 2026-04-13

**My approach:** Dict of magazine letter counts, decrement as you read ransom note, fail on zero/missing.

**Where I went off track:** Nothing. Solution is correct.

**Optimal approach:**
- `Counter(magazine)`.
- For each char in ransom, if count is zero return False, else decrement.
- One-liner: `not (Counter(ransom) - Counter(magazine))`.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">ransom="aa" magazine="aab"</text>
  <g font-family="monospace" font-size="13">
    <text x="60" y="70" fill="#4A90D9">supply: a:2 b:1</text>
    <text x="60" y="100" fill="#4A90D9">take a → a:1; take a → a:0</text>
    <text x="60" y="130" fill="#27AE60">all supplied → True</text>
  </g>
</svg>

**Complexity:** Mine O(n+m) / O(1) → Optimal O(n+m) / O(1)

**Takeaway:** Supply vs demand counts is a one-pass pattern — no need for two dicts.
