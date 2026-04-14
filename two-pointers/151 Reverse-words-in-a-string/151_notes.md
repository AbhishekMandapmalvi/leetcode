# #151 — Reverse Words in a String

> **Difficulty:** Medium | **Patterns:** String, Two Pointers | **Date:** 2026-04-13

**My approach:** `s.strip()` then `" ".join(s.split()[::-1])` — the idiomatic one-liner.

**Where I went off track:** Nothing major. Second attempt manually popped empty strings from `split(" ")`, which is what `split()` (no arg) does for free.

**Optimal approach:**
- `s.split()` with no arg collapses runs of whitespace automatically.
- Reverse the list.
- Join with single spaces.
- For in-place, use the 3-step: reverse whole string, reverse each word, compact spaces.

**Visual:**
<svg viewBox="0 0 600 180" width="100%" xmlns="http://www.w3.org/2000/svg">
  <text x="300" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#2C3E50">"  the  sky is blue  "</text>
  <g font-family="monospace" font-size="13" fill="#2C3E50">
    <text x="300" y="55" text-anchor="middle" fill="#4A90D9">split() → ["the","sky","is","blue"]</text>
    <text x="300" y="90" text-anchor="middle" fill="#4A90D9">[::-1] → ["blue","is","sky","the"]</text>
    <text x="300" y="125" text-anchor="middle" fill="#27AE60">join → "blue is sky the"</text>
  </g>
</svg>

**Complexity:** Mine O(n) / O(n) → Optimal O(n) / O(n) (or O(1) in-place on char array)

**Takeaway:** `str.split()` without an argument collapses whitespace — don't reimplement it.
